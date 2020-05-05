from flask.app import HTTPException
from sqlalchemy.orm import sessionmaker
import sys
import pandas as pd
from io import StringIO
from sklearn.linear_model import Ridge
from sklearn.utils.extmath import safe_sparse_dot
from flask import Flask, request, jsonify, abort
from sklearn.model_selection import KFold, GridSearchCV

from regression.db import init_db, Model, new_engine


def create_app():
    engine = new_engine()
    if engine is None:
        sys.exit(1)

    session_factory = sessionmaker(bind=engine)

    app = Flask(__name__)

    @app.errorhandler(Exception)
    def error_handler(exc):
        if isinstance(exc, HTTPException):
            return jsonify({'error': exc.description}), exc.code
        return jsonify({'error': 'internal error'}), 500

    @app.route('/train', methods=['POST'])
    def create_model():
        data = request.get_json()
        try:
            model_jsonb, cv_results_jsonb = train(data)
        except Exception as exc:
            abort(400, f'Could not train your data due to the exception: {exc}')
            return

        session = session_factory()
        model = Model(model=model_jsonb, cv_results=cv_results_jsonb)
        session.add(model)
        session.commit()
        #    session.close()

        return jsonify({'model_id': model.id})

    @app.route('/model/<int:model_id>', methods=['GET'])
    def get_model(model_id):
        session = session_factory()
        model = session.query(Model).filter_by(id=model_id).first()
        if model is None:
            abort(404, f'model with ID  {model_id} not found')
            return
        return jsonify({
            'model': model.model['model'],
            'cv_results': model.cv_results['cv_results'],
        })

    @app.route('/test', methods=['POST'])
    def test():
        data = request.get_json()
        try:
            model_id = int(data['model_id'])
            csv = StringIO(data['data'])
            csv = pd.read_csv(csv, sep=",")
            session = session_factory()
            model = session.query(Model).filter_by(id=model_id).first()
            if model is None:
                abort(404, f'video {model_id} not found')
                return
            model = model.model
            result = predict(csv, model)
            return jsonify({'result: ': result})
        except Exception as exc:
            abort(400, f'Could not train your data due to the exception: {exc}')
            return

    app.run()


def train(data):
    target = str(data['target'])
    fit_intercept = bool(data['fit_intercept'])
    n_folds = int(data['n_folds'])
    param_grid = dict(alpha=list(data['l2_coef']))
    csv = StringIO(data['data'])
    csv = pd.read_csv(csv, sep=",")
    X = csv.drop(target, axis=1)
    y = csv[target]
    kf = KFold(n_splits=n_folds)
    ridge = Ridge(fit_intercept=fit_intercept)
    grid = GridSearchCV(estimator=ridge,
                        param_grid=param_grid,
                        scoring="neg_mean_squared_error",
                        cv=kf,
                        n_jobs=-1,
                        iid=True)
    grid_result = grid.fit(X, y)
    model = Ridge(fit_intercept=fit_intercept, alpha=grid_result.best_params_['alpha'])
    model.fit(X, y)
    dict_inter_coef = {'intercept': model.intercept_, 'coef': dict(zip(list(X), model.coef_.tolist()))}
    model_jsonb = {'model': dict_inter_coef}

    list_cv_results = []
    cv_results_jsonb = {}
    for i in range(len(data['l2_coef'])):
        d = {}
        mse = grid_result.cv_results_['mean_test_score'][i]
        l2coef = data['l2_coef'][i]
        d['param_value'] = l2coef
        d['mean_mse'] = -mse
        list_cv_results.append(d)
    cv_results_jsonb["cv_results"] = list_cv_results

    return model_jsonb, cv_results_jsonb


def predict(csv, model):
    result = []
    w = pd.DataFrame(data=model['model']['coef'], index=[0])
    b = model['model']['intercept']
    for row in range(csv.shape[0]):
        a = csv.loc[row]
        result.append(float(safe_sparse_dot(a, w.T) + b))
    return result

# python
# import regression.app
# regression.app.create_app()

# ДЛЯ ПЕРВОЙ РУЧКИ
# json = {"data": "a,b,c,d\n2,3,4,45\n4,9,16,3\n8,81,64,67\n16,243,256,1\n32,729,1024,3", "target": "a", "n_folds": 5, "fit_intercept": "true", "l2_coef": [1.0, 10.0, 100.0]}
# r = requests.post('http://127.0.0.1:5000/train', json=json); (r.status_code, r.json())

# ДЛЯ ВТОРОЙ РУЧКИ
# r = requests.get("http://127.0.0.1:5000/model/7", json={}); (r.status_code, r.json())

# ДЛЯ ТРЕТЬЕЙ РУЧКИ
# r = requests.post('http://127.0.0.1:5000/test', json={"data": "b,c,d\n3,4,45\n9,16,3\n81,64,67\n243,256,1\n729,1024,3", "model_id": 4}); (r.status_code, r.json())
