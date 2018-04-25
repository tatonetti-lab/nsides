import React from 'react';
import { Redirect } from 'react-router-dom';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';

class PrivateRoute extends React.Component {
  constructor (props) {
    super (props);
  }

  render () {
    const { session, Component, history } = this.props;
    if (session) {
      return <Component/>
    } else {
      // history.push('/login');
      window.location.href = '/login';
    }
  }
}

const mapStateToProps = (state) => {
  const session = state.User.session;
  return {
    session
  }
}

const mapDispatcherToProps = (dispatch) => {
  return {
    
  }
}

export default withRouter(connect(mapStateToProps, mapDispatcherToProps)(PrivateRoute));