from utility import rest_server, daemon, config_manager
from flask import Blueprint, jsonify, request

ac_router = Blueprint('ac_router', __name__, url_prefix='/api/v1')


@ac_router.route('/query_winner', methods=['get'])
def get_win_prob():
    params = request.args.get('params')
    rlt = jsonify({
        "result": "success",
        "win_probability": "70",
        "winner": "5",
        "msg": ""
    })
    return rlt


class PredServiceDaemon(daemon.Daemon):
    def setup_server(self):
        server = rest_server.RestServer(ip=config_manager.config['rest_server']['ip'],
                                        port=config_manager.config['rest_server']['port'])
        server.register_router(ac_router)
        self.server = server


if __name__ == '__main__':
    PredServiceDaemon().main()
