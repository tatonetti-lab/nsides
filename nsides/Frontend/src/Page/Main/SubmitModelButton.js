import React from 'react';

class SubmitModelButton extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        drugToSubmit: this.props.drugName 
      };
      this.handleSubmitClick = this.handleSubmitClick.bind(this);
    }

    handleSubmitClick(e) {
        console.log(e);
        console.log(this.state.drugToSubmit);
    }

    render() {
      return (
        <div>
          <button
            name='submit-button'
            value='submit'
            onClick={this.handleSubmitClick}>
          <a href="/jobsubmission">
            Submit model
          </a>
          </button>
        </div>
      );
    }
}

export default SubmitModelButton;