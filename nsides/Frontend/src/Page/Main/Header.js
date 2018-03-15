import React from 'react';

const Header = (props) => {
  return <div id="header">
    <div id="header-content">
      <div id="login-link">
        <a href="/login">
          log in
        </a>
      </div>
      <div>
        <h1 className="logo-h1">
          <a href="/">
            <img src="../../../dist/images/nsides-logo.svg" alt='loading'>
              nSides
            </img>
          </a>
        </h1>
        <h3>A comprehensive database of drug-drug(s)-effect relationships</h3>
      </div>
    </div>
    <div id="bar"></div>
  </div>;
};

export default Header;