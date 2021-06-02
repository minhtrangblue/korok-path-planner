from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from core.process import simulatedAnnealling
import json


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # initialise map
    @app.route('/')
    def init_map():
        return render_template('map.html')

    # function call on user request find path
    @app.route('/', methods=['GET', 'POST'])
    def compute_path():
        # POST request
        if request.method == 'POST':
            response = request.get_json()['features']
            if len(response) == 0:
                app.logger.info('Empty response. No area selected')
                paths = [[]]
                costs = [-1]
            else:
                paths = [[] for _ in response]
                costs = [-1 for _ in response]
                for i in range(len(response)):
                    selected_rectangle = response[i]['geometry']['coordinates'][0]
                    # app.logger.info('Selected area cost:' + str(response[i]['properties']['pathcost']))
                    # get the nodes in selected area
                    selected_x_min = min([point[0] for point in selected_rectangle])
                    selected_x_max = max([point[0] for point in selected_rectangle])
                    selected_y_min = min([point[1] for point in selected_rectangle])
                    selected_y_max = max([point[1] for point in selected_rectangle])
                    df = pd.read_csv('data/all_seeds.csv')
                    nodes = df[(df['y'] > selected_y_min) & (df['y'] < selected_y_max)
                               & (df['x'] > selected_x_min) & (df['x'] < selected_x_max)]
                    nodes = np.array(nodes[['x', 'y']]).transpose()
                    # app.logger.info('Selected nodes:' + json.dumps(nodes.tolist()))
                    if nodes.shape[1] <= 1:
                        app.logger.info('Select more than 1 node')
                        paths[i] = []
                        costs[i] = -1
                    else:
                        sa = simulatedAnnealling(nodes=nodes)
                        if nodes.shape[1] <= 8:
                            # if fewer than 8 nodes run exact algorithm
                            app.logger.info('Run exact algorithm...')
                            shortest_path, cost_best = sa.calExactPath()
                        else:
                            # if more than 8 nodes run estimation
                            app.logger.info('Running Simulated Annealling ...')
                            shortest_path, cost_best = sa.optimise()

                        shortest_path = shortest_path[::-1, :].transpose().tolist()
                        app.logger.info('Finished.')
                        paths[i] = shortest_path
                        costs[i] = cost_best
            # send result in a dict
            result = dict()
            result['paths'] = paths
            result['costs'] = costs
            return jsonify(result)
    return app
