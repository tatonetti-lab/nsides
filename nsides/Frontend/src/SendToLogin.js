import React from 'react';

class SendToLogin extends React.Component {
  constructor (props) {
    super (props);
  }

  componentWillMount () {
    window.location.href = '/login';
  }

  render () {
    return <div className='center'>
      Need to Log In
    </div>
  }
}

export default SendToLogin;