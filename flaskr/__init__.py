import os
from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from core.process import simulatedAnnealling
import json


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def init_map():
        return render_template('map.html')

    @app.route('/', methods=['GET', 'POST'])
    def get_selected_area():
        # POST request
        if request.method == 'POST':
            response = request.get_json()['features']
            if len(response) == 0:
                app.logger.info('Empty response. No area selected')
                return jsonify([])
            else:
                paths = [[] for _ in response]
                for i in range(len(response)):
                    selected_rectangle = response[i]['geometry']['coordinates'][0]
                    # app.logger.info('Selected area:' + str(selected_rectangle))
                    # get the nodes in selected area
                    selected_x_min = min([point[0] for point in selected_rectangle])
                    selected_x_max = max([point[0] for point in selected_rectangle])
                    selected_y_min = min([point[1] for point in selected_rectangle])
                    selected_y_max = max([point[1] for point in selected_rectangle])
                    df = pd.read_csv('data/all_seeds.csv')
                    nodes = df[(df['y'] > selected_y_min) & (df['y'] < selected_y_max) & (df['x'] > selected_x_min) & (df['x'] < selected_x_max)]
                    nodes = np.array(nodes[['x', 'y']]).transpose()
                    # app.logger.info('Selected nodes:' + json.dumps(nodes.tolist()))
                    if nodes.shape[1] <= 1:
                        app.logger.info('Select more than 1 node')
                        paths[i] = []

                    else:
                        sa = simulatedAnnealling(nodes=nodes)
                        if nodes.shape[1] <= 8:
                            # if fewer than 8 nodes run exact algorithm
                            app.logger.info('Run exact algorithm...')
                            shortest_path, _ = sa.calExactPath()
                        else:
                            # if more than 8 nodes run estimation
                            app.logger.info('Running Simulated Annealling ...')
                            shortest_path, _ = sa.optimise()

                        shortest_path = shortest_path[::-1, :].transpose().tolist()
                        app.logger.info('Finished:' + json.dumps(shortest_path))
                        paths[i] = shortest_path

                return jsonify(paths)


    return app

