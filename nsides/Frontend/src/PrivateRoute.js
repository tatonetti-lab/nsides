import React from 'react';
import { Redirect } from 'react-router-dom';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import SendToLogin from './SendToLogin';

class PrivateRoute extends React.Component {
  constructor (props) {
    super (props);
  }

  render () {
    let { session, component:Component, history } = this.props;
    print('session', session);
    if (session.name) {
      return <Component/>;
    } else {
      // history.push('/login');
      return <SendToLogin/>;
    }
  }
}

const mapStateToProps = (state) => {
  const session = state.UserReducer.session;
  return {
    session
  };
}

const mapDispatcherToProps = (dispatch) => {
  return {
    
  };
}

export default withRouter(connect(mapStateToProps, mapDispatcherToProps)(PrivateRoute));