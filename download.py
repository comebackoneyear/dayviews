#!/usr/bin/env python
import urllib
import urllib2
import json
import os


class dayviews():
    API_KEY = "bd2c8c977624f9c7d64bb683ffc2a0a341ecc825"
    API_SECRET = "5hpz0piIRWH8DsbRvU8X8BBpsDYx"
    API_ENDPOINT = "https://api.dayviews.com/"
    USERNAME = ""
    PASSWORD = ""
    SAVE_DIR = "download"

    FORCE_DOWNLOAD = False

    userid = None

    def __init__(self):
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='api.dayviews.com',
                                  uri=self.API_ENDPOINT,
                                  user=self.USERNAME,
                                  passwd=self.PASSWORD)
        self.opener = urllib2.build_opener(auth_handler)
        self.get_login_status()

    def get_json(self, uri, **kwargs):
        kwargs["api_key"] = self.API_KEY
        args = urllib.urlencode(kwargs)
        url = "%s%s?%s" % (self.API_ENDPOINT, uri, args)
#        print url
        try:
            req = self.opener.open(url)
        except urllib2.HTTPError as e:
            print "Request failed: %d" % e.code
            return {}
        ret = req.read()
        try:
            return json.loads(ret)
        except:
            raise

    def get_login_status(self):
        ret = self.get_json("login_status.json")
        if ret and ret.get("userid"):
            self.userid = int(ret.get("userid"))
            return ret

    def _get_years(self):
        uri = "/users/%d/images/dates.json" % self.userid
        years = self.get_json(uri).get("years")
        self.write_json_file("years.json", years)
        return years

    def _get_months(self, year):
        uri = "/users/%d/images/dates/%s.json" % (self.userid, year)
        months = self.get_json(uri).get("months")
        self.write_json_file(
            "months.json", months, wdir=str(year))
        return months

    def _get_days(self, year, month):
        days = None
        if not self.FORCE_DOWNLOAD:
            try:
                fp = open(
                    "%s/json/%s/%s/days.json" % (self.SAVE_DIR, year, month))
                data = fp.read()
                days = json.loads(data)
                print "using cached"
            except:
                pass

        if days is not None:
            uri = "/users/%d/images/dates/%s/%s.json" % (
                self.userid, year, month)
            days = self.get_json(uri).get("days")
            self.write_json_file(
                "days.json", days, wdir="%s/%s" % (year, month))
        return days

    def get_all_images(self):
        for y in self._get_years():
            for m in self._get_months(y):
                for d in self._get_days(y, m):
                    print "Processing %s-%s-%s" % (y, m, d)
                    uri = "/users/%d/images/dates/%s/%s/%s.json" % (
                        self.userid, y, m, d)
                    images = self.get_json(uri)
                    self.write_json_file("%s.json" % d, images.get(
                        "images"), wdir="%s/%s" % (y, m))
                    for i in images.get("images"):
                        uri = "/users/%d/images/dates/%s/%s/%s/comments.json" \
                            % (self.userid, y, m, d)
                        comments = self.get_json(uri)
                        i["comments"] = comments
                        if i.get("fullsize"):
                            url = i.get("fullsize").pop("1900x1000")
                            if url:
                                url = url.replace(
                                    "/f/b/", "/f/o/")  # original hd file
                        else:
                            url = i.get("image")
                        download = self.download_image_file(
                            url, "%s/%s/%s" % (y, m, d), i["id"])
                        i["local_image"] = download
                        self.write_json_file("image_%s.json" % i.get(
                            "id"), i, wdir="%s/%s" % (y, m))
#                        return
#                        print "%s %s %s: %s" % (y,m,d,i.get("image"))

    def write_json_file(self, filename, data_dict, wdir=None):
        if wdir:
            wdir = "%s/json/%s" % (self.SAVE_DIR, wdir)
        else:
            wdir = "%s/json" % self.SAVE_DIR
        try:
            os.makedirs(wdir)
        except:
            pass
        try:
            fp = open("%s/%s" % (wdir, filename), "w")
            fp.write(json.dumps(data_dict))
            fp.close()
            return True
        except:
            raise
            return False

    def download_image_file(self, url, wdir, filename):
        return "/images/%s/%s" % (wdir, filename)
        try:
            output_filename = "%s/images/%s" % filename
            f = urllib2.urlopen(url)
            img = f.read()
            open(output_filename, 'wb').write(img)
            return "/images/%s" % filename
        except:
            return None

dv = dayviews()
dv.get_all_images()
