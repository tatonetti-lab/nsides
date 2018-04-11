import React from 'react';

class Joblist extends React.Component {
  constructor (props) {
    super (props);
  }

  render () {
    return <div className="job-container container">
      <div className="page-header">
        <h1>nSides compute jobs</h1>
      </div>

      <div className="row">
        <table className="table table-bordered">
          <tbody>
            <th>ID</th>
            <th>Name</th>
            <th>Execution system</th>
            <th>Application</th>
            <th>Status</th>
            <th>Owner</th>
            <th>Start Time</th>
            <th>End Time</th>

            {/* {%if joblist[0]%} {%for job in joblist[1]%} */}
            {/* <tr>
              <td>{ job['id'] }</td>
              <td>{ job['name'] }</td>
              <td>{ job['executionSystem'] }</td>
              <td>{ job['appId'] }</td>
              <td>{ job['status'] }</td>
              <td>{ job['owner'] }</td>
              <td>{ job['startTime'] }</td>
              <td>{ job['endTime'] }</td>
            </tr>
            {/* {%endfor%} {%else%} */}
            {/* <p>No jobs found.</p> */}
            {/* {%endif%} */}
          </tbody>
        </table>
      </div>
    </div>
  }
}

export default Joblist;