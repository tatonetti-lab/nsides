import React, { Component } from 'react';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import axios from 'axios';
import { updateUserSession } from './Redux/Actions/UserActions';
import Header from './Header';
import './css/main.css';
import './css/fonts.css';
// import './css/login.css';
// import Actions from './Redux/Actions/Actions';
// import { push } from 'react-router-redux';

class App extends Component {
  constructor (props) {
    super (props);
  }

  componentWillMount () {
    const { boundUpdateUserSession } = this.props;

    axios({
      method: 'GET',
      url: '/session'
    }).then(result => {
      const data = result.data;
      // console.log('session', result, data, updateUserSession);
      boundUpdateUserSession(data);
    })
  }

  render() {
    let { requestedSession } = this.props;
    if (requestedSession) {
      return (
        <div className="Application">
          <Header/>
          { 
            this.props.children 
          }
        </div>
        );
    } else {
      return <div></div>
    }
  }
}

const mapStateToProps = (state) => {
  // console.log('state is ',state);
  let requestedSession = state.UserReducer.requestedSession;
  return { 
    requestedSession
  };
};

const mapDispatchToProps = (dispatch) => {
  return {
    boundUpdateUserSession: (session) => {
      dispatch(updateUserSession(session));
    }
  };
};

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(App));