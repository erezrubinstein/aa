
class MockRDSAccess(object):
    def __init__(self):
        self.files = []

    def call_post_file(self, rds_path, f, context, metadata=None):
        self.files.append((rds_path, f.get("file", [None])[0]))
        return {"/".join([rds_path, f["file"][0]]): "fake_object_id"}

    def call_get_latest_in_path(self, path):
        return "use mox, please!"