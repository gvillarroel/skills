#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2,<3", "scikit-learn>=1.7,<2"]
# ///
"""Measure a small grouped regression experiment without test-set tuning."""
import hashlib
import json
from pathlib import Path
import numpy as np
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, GridSearchCV, learning_curve
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

ROOT=Path(__file__).resolve().parent.parent


def model(degree,alpha):
    return Pipeline([('poly',PolynomialFeatures(degree=degree,include_bias=False)),('scale',StandardScaler()),('ridge',Ridge(alpha=alpha))])


def main():
    rng=np.random.default_rng(23);group_x=rng.uniform(-1,1,120);groups=np.repeat(np.arange(120),2)
    X=(np.repeat(group_x,2)+rng.normal(0,.015,240)).reshape(-1,1)
    y=np.sin(3*X[:,0])+.3*X[:,0]+np.repeat(rng.normal(0,.08,120),2)+rng.normal(0,.23,240)
    development,test=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=31).split(X,y,groups))
    a,b=next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=47).split(X[development],y[development],groups[development]))
    train,validation=development[a],development[b]
    assert not(set(groups[train])&set(groups[validation]) or set(groups[train])&set(groups[test]) or set(groups[validation])&set(groups[test]))
    cv=GroupKFold(n_splits=5)
    search=GridSearchCV(model(3,1),{'poly__degree':[1,3,5,9,17],'ridge__alpha':[.000001,.01,.3,10]},cv=cv,scoring='neg_mean_squared_error',return_train_score=True,n_jobs=1)
    search.fit(X[train],y[train],groups=groups[train])
    table=[]
    for i,p in enumerate(search.cv_results_['params']):
        table.append({'degree':p['poly__degree'],'alpha':p['ridge__alpha'],'trainMSE':-float(search.cv_results_['mean_train_score'][i]),'cvMSE':-float(search.cv_results_['mean_test_score'][i]),'cvSD':float(search.cv_results_['std_test_score'][i])})
    chosen=search.best_estimator_;validation_mse=mean_squared_error(y[validation],chosen.predict(X[validation]))
    baseline=DummyRegressor().fit(X[train],y[train])
    baseline_validation=mean_squared_error(y[validation],baseline.predict(X[validation]))
    sizes,learning_train,learning_cv=learning_curve(chosen,X[train],y[train],groups=groups[train],cv=GroupKFold(5),train_sizes=[.35,.5,.7,1],scoring='neg_mean_squared_error',shuffle=True,random_state=71)
    grid=np.linspace(-1.05,1.05,180).reshape(-1,1)
    fits=[]
    for degree,alpha in [(1,.000001),(5,.3),(17,.000001)]:
        fitted=model(degree,alpha).fit(X[train],y[train])
        fits.append({'degree':degree,'alpha':alpha,'prediction':fitted.predict(grid).tolist()})
    # Freeze all choices before the single final holdout evaluation.
    best=search.best_params_;final=model(best['poly__degree'],best['ridge__alpha']).fit(X[development],y[development])
    final_test=mean_squared_error(y[test],final.predict(X[test]))
    squared=(y[test]-final.predict(X[test]))**2
    held_groups=np.unique(groups[test]);bootstrap_rng=np.random.default_rng(103)
    cluster_errors=np.array([squared[groups[test]==g].mean() for g in held_groups])
    bootstrap=bootstrap_rng.choice(cluster_errors,(4000,len(held_groups)),replace=True).mean(axis=1)
    interval=np.quantile(bootstrap,[.025,.975]).tolist()
    report={'dataStatus':'synthetic measured experiment','seed':23,'groups':120,'samples':240,'split':{'train':len(train),'validation':len(validation),'test':len(test),'groupsDisjoint':True,'percent':[60,20,20]},'samplesXY':[[float(X[i,0]),float(y[i]),'train' if i in set(train) else 'validation' if i in set(validation) else 'test',int(groups[i])] for i in range(len(y))],'gridX':grid[:,0].tolist(),'fits':fits,'candidates':table,'best':best,'baselineValidationMSE':float(baseline_validation),'chosenValidationMSE':float(validation_mse),'finalTestMSE':float(final_test),'testEvaluations':1,'folds':5,'learning':[{'samples':int(n),'trainMSE':float(-a.mean()),'cvMSE':float(-b.mean())} for n,a,b in zip(sizes,learning_train,learning_cv)],'earlyStopping':{'dataStatus':'schematic, not a Ridge training trace','epoch':list(range(31)),'trainLoss':[float(.8*np.exp(-i/5)+.055) for i in range(31)],'validationLoss':[float(.8*np.exp(-i/5)+.105+max(0,i-12)**2*.0011) for i in range(31)]}}
    report['testMSEInterval95']=interval
    report['intervalMethod']='Percentile cluster bootstrap of fixed-model holdout errors, 4000 replicates, seed 103; conditional on this fitted model and sampled entities.'
    report['regularization']=[{'alpha':alpha,'coefficientNorm':float(np.linalg.norm(model(17,alpha).fit(X[train],y[train]).named_steps['ridge'].coef_))} for alpha in [.000001,.01,.3,10]]
    out=ROOT/'artifacts/data';out.mkdir(parents=True,exist_ok=True)
    target=out/'experiment.json';target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ok':True,'samples':len(y),'best':best,'baselineValidationMSE':baseline_validation,'chosenValidationMSE':validation_mse,'testMSE':final_test,'testEvaluations':1,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))
    return 0


if __name__=='__main__':raise SystemExit(main())
