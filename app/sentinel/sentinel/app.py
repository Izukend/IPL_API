import falcon
from sentinel.abuse import Abuse_report

app = application = falcon.App()

abuse = Abuse_report()
app.add_route('/abuse', abuse)