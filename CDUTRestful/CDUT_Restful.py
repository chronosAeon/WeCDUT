import sys, os

print(os.path.abspath('..'))
sys.path.append(os.path.abspath('..'))
from CDUTRestful.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=app.config['DEBUG'], port=443, threaded=True, ssl_context=(
        '1_chronos.fzerolight.cn_bundle.crt', '2_chronos.fzerolight.cn.key'))
