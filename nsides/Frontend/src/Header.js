import React from 'react';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';

class Header extends React.Component {
  constructor (props) {
    super (props);
  }

  render () {
    // console.log(this);
    let { session } = this.props;
    let logIn = session.name ? (
      <div id="login-link">
        <a href="/logout">log out</a>
        <br/>
        Current user: <a href="/profile">{session.name}</a>
        <br/>
        <a href="/joblist">View submitted jobs</a>
      </div>
    ) : (
      <div id="login-link">
        <a href="/login">
          log in
        </a>
      </div>
    );

    return <div id="header">
      <div id="header-content">
        { logIn }
        <div>
          <h1 className="logo-h1">
            <a href="/">
              <img className='nsides-logo' src="../../../dist/images/nsides-logo.svg" alt='loading'/>
              nSides
            </a>
          </h1>
          <h3>
            A comprehensive database of drug-drug(s)-effect relationships
          </h3>
        </div>
      </div>
      <div id="bar"></div>
    </div>;
  }
};

const mapStateToProps = (state) => {
  const session = state.UserReducer.session;
  return {
    session
  }
}

const mapDispatcherToProps = (dispatch) => {
  return {
    
  }
}
export default withRouter(connect(mapStateToProps, mapDispatcherToProps)(Header));