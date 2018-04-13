import React from 'react';
import '../../css/profile/profile.css';
import axios from 'axios';

class Profile extends React.Component {
  constructor (props) {
    super (props);
    this.state = {
      name: '',
      email: '',
      institution: ''
    };
    this.handleChange = this.handleChange.bind(this);
  }

  componentDidMount () {
    axios({
      method: 'GET',
      url: '/profile/data'
    }).then((result) => {
      // console.log(result);
      let data = result.data;
      this.setState(data);
    })
  }

  handleChange (e) {
    let type = e.target.id;
    this.setState({
      [type] : e.target.value
    })
  }

  render () {
    return <div className="profile-container container">
      <h2>
        User Profile information
      </h2>

      <form role="form" action="/profile/data" method="POST">
        <div className="form-group">
          <label htmlFor="name">Name</label>
          <input 
            onChange={this.handleChange}
            type="text" 
            className="form-control" 
            id="name" 
            name="name" 
            placeholder="full name" 
            required="required" 
            tabIndex="1" 
            value={this.state.name}/>
        </div>

        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input 
            onChange={this.handleChange}
            type="email" 
            id="email" 
            name="email" 
            className="form-control" 
            placeholder="me@example.com" 
            required="required" 
            tabIndex="2"
            value={this.state.email}/>
        </div>

        <div className="form-group">
          <label htmlFor="institution">Institution/Department</label>
          <input 
            onChange={this.handleChange}
            type="text" 
            id="institution" 
            name="institution" 
            className="form-control" 
            required="required" 
            tabIndex="3" 
            value={this.state.institution}/>
        </div>

        <div className="form-group">
          <button type="submit" className="btn btn-primary">Save/Update</button>
        </div>
      </form>
    </div>
  }
}

export default Profile;