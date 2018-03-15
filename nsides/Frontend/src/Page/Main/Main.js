import React from 'react';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import Header from './Header';
import '../../css/main.css';
// import axios from 'axios';
// import Actions from '../../Redux/Actions/Actions';

class Main extends React.Component {
  constructor (props) {
    super (props);
    this.state = {

    }
  }
  render () {
    return <div id='content'>
      <Header/>
    </div>;
  }
}

const mapStateToProps = (state) => {
  return {};
};
  
const mapDispatchToProps = (dispatch) => {
  return {};
};

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Main));