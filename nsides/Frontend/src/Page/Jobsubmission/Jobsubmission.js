import React from 'react';
import { conceptIdDrugs } from '../../Helpers/drugs-top-200';
import Select from 'react-select';
import '../../css/jobsubmission/jobsubmission.css';
import '../../css/react-select.css';

class Jobsubmission extends React.Component {
  constructor (props) {
    super (props);
    this.state = {
      options: conceptIdDrugs,
      value: []
    }
    this.handleSelectChange = this.handleSelectChange.bind(this);
  }

  handleSelectChange(value) {
    this.setState({value}, () =>{
      this.fetchDrugIndices();
    });
  }

  render () {
    return <div className="container">
      <div id="job_submit_container">
        <form action="/jobsubmission/submit-job" className="form-signin form-submitjob" method="POST">
          {/* <div className="form-group">
            <div className="drug_title">Model type</div>
            <select className="form-control" name="mtype">
              <option value="dnn">DNN</option>
              <option value="lrc">LRC</option>
            </select>
          </div> */}
          <div className="form-group submit-select-container">
            <div className="drug_title">Drug(s)</div>
            <Select name="model_index" joinValues multi simpleValue
              value={this.state.value}
              placeholder="Select drug(s)..."
              noResultsText="Drug(s) not found"
              options={this.state.options}
              onChange={this.handleSelectChange} />
          </div>
          <div className="form-group">
            <input className="btn btn-lg btn-primary btn-block" type="submit" value="Submit job" />
          </div>
        </form>
      </div>

    </div>
  }
}

export default Jobsubmission