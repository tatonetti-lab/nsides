import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { createStore, combineReducers, applyMiddleware, compose } from 'redux';
import { Provider } from 'react-redux';
import createHistory from 'history/createBrowserHistory';
import { Route, Switch, /*Redirect*/ } from 'react-router';
import { ConnectedRouter, routerReducer, routerMiddleware } from 'react-router-redux';
import Reducers from './Redux/Reducers/Reducers';
import PrivateRoute from './PrivateRoute';
import Main from './Page/Main/Main';
import Jobsubmission from './Page/Jobsubmission/Jobsubmission';
import Profile from './Page/Profile/Profile';
import Joblist from './Page/Joblist/Joblist';
import Handle404 from './Handle404';

// Create a history of your choosing (we're using a browser history in this case)
const history = createHistory();

// Build the middleware for intercepting and dispatching navigation actions
const middleware = routerMiddleware(history);

// const composeEnhancers = typeof window === 'object' && 
//     window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ ?   
//     window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__({
//       // Specify extension’s options like name, actionsBlacklist, actionsCreators, serialize...
//     }) : compose;

// Add the reducer to your store on the `router` key
// Also apply our middleware for navigating
const store = createStore(
  combineReducers({
    ...Reducers,
    router: routerReducer
  }),
  compose(
    applyMiddleware(middleware)
  )
);

let app = (
  <Provider store={store}>
    <ConnectedRouter history={history}>
      <App>
        {
          <Switch>
            <Route exact path="/" render={() => {
              return <Main/>;
            }}/>
            <PrivateRoute exact 
              path="/jobsubmission"  
              component={Jobsubmission}/>
            <PrivateRoute exact 
              path="/joblist"  
              component={Joblist}/>
            <PrivateRoute exact 
              path="/profile"  
              component={Profile}/>
            {/* <Route exact path="/jobsubmission" render={() => {
              return <Jobsubmission/>;
            }}/>
            <Route exact path="/joblist" render={() => {
              return <Joblist/>;
            }}/>
            <Route exact path="/profile" render={() => {
              return <Profile/>;
            }}/> */}
            <Route path="*" component={Handle404} status={404}/>
          </Switch>
        }
      </App>
    </ConnectedRouter>
  </Provider>
);

ReactDOM.render(
  app,
  document.getElementById('app')
);