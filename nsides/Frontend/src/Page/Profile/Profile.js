import React from 'react';
import '../../css/profile/profile.css';

class Profile extends React.Component {
  constructor (props) {
    super (props);
    
  }

  render () {
    return <div className="profile-container container">
      <h2>
        User Profile information
      </h2>

      <form role="form" action="/profile" method="POST">
        <div className="form-group">
          <label htmlFor="name">Name</label>
          <input 
            readOnly
            type="text" 
            className="form-control" 
            id="name" 
            name="name" 
            placeholder="full name" 
            required="required" 
            tabIndex="1" 
            value="{{session['name']}}"/>
        </div>

        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input 
            readOnly
            type="email" 
            id="email" 
            name="email" 
            className="form-control" 
            placeholder="me@example.com" 
            required="required" 
            tabIndex="2"
            value="{{session['email']}}"/>
        </div>

        <div className="form-group">
          <label htmlFor="institution">Institution/Department</label>
          <input 
            readOnly
            type="text" 
            id="institution" 
            name="institution" 
            className="form-control" 
            required="required" 
            tabIndex="3" 
            value="{{session['institution']}}"/>
        </div>

        <div className="form-group">
          <button type="submit" className="btn btn-primary">Save/Update</button>
        </div>
      </form>
    </div>
  }
}

export default Profile;