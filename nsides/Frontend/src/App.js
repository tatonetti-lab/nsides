import React, { Component } from 'react';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
// import Actions from './Redux/Actions/Actions';
// import { push } from 'react-router-redux';
// import axios from 'axios';

class App extends Component {

  componentDidMount () {
  
  }

  render() {
    return (
      <div className="Application">
        { this.props.children }
      </div>
    );
  }
}

const mapStateToProps = (state) => {
  //console.log('state is ',state);
  return { 
  }
};

const mapDispatchToProps = (dispatch) => {
  return {
  }
};

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(App));