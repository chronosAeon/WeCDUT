from . import CDUT_Restful

@CDUT_Restful.route('/godhelpme')
def help():
    return 'help,help,help'