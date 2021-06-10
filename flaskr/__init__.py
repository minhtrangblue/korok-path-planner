from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from core.optimiser import SimulatedAnnealing, ExactOptimiser
from core.solver import Solver
from core.mpsolver import MPSolver
import traceback


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # initialise map
    @app.route('/')
    def init_map():
        return render_template('map.html')

    def parse_response(response):
        response = response['features']
        nodes = [[] for _ in response]
        if len(response) == 0:
            # app.logger.info('Empty response. No area selected')
            nodes = [[[]]]
        else:
            for i in range(len(response)):
                selected_rectangle = response[i]['geometry']['coordinates'][0]
                # get the nodes in selected area
                selected_x_min = min([point[0] for point in selected_rectangle])
                selected_x_max = max([point[0] for point in selected_rectangle])
                selected_y_min = min([point[1] for point in selected_rectangle])
                selected_y_max = max([point[1] for point in selected_rectangle])
                df = pd.read_csv('data/all_seeds.csv')
                locations = df[(df['y'] > selected_y_min) & (df['y'] < selected_y_max)
                           & (df['x'] > selected_x_min) & (df['x'] < selected_x_max)]
                locations = np.array(locations[['x', 'y']]).transpose()
                nodes[i] = locations.tolist()
        app.logger.info('Selected nodes:' + str(nodes))
        return nodes

    # function call on user request find path
    @app.route('/', methods=['GET', 'POST'])
    def compute_path():
        # POST request
        if request.method == 'POST':
            response = request.get_json()
            nodes = parse_response(response)
            if len(nodes) == 0:
                app.logger.info('Empty response. No area selected')
                paths = [[]]
                costs = [-1]
            else:
                paths = [[] for _ in nodes]
                costs = [-1 for _ in nodes]
                for i in range(len(nodes)):
                    try:
                        if len(nodes[i]) == 0 or len(nodes[i][0]) <= 1:
                            app.logger.info('Select more than 1 node')
                            paths[i] = []
                            costs[i] = -1
                        else:
                            app.logger.info('Find path for nodes:' + str(str(nodes[i])))
                            if len(nodes[i][0]) <= 8:
                                s = Solver(ExactOptimiser(nodes=nodes[i]))
                            else:
                                s = MPSolver(SimulatedAnnealing(nodes=nodes[i]))
                            shortest_path, cost_best = s.solve()
                            app.logger.info('Finished.' + str(shortest_path))
                            paths[i] = list(map(list, zip(*shortest_path[::-1])))
                            costs[i] = cost_best
                    except Exception as e:
                        app.logger.error(traceback.print_exception(type(e), e, e.__traceback__))
            # send result in a dict
            result = dict()
            result['paths'] = paths
            result['costs'] = costs
            return jsonify(result)
    return app
