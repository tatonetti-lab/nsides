import React from 'react';
import { modelToColor } from './graphing';

class lineGraphToggle extends React.Component {
  constructor (props) {
    super (props);
    this.state = {
      status: 'remove'
    };
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick (e) {
    e.preventDefault();
    const graphInfo = this.props.graphInfo;
    const model = graphInfo.model;
    const modelClass = model + '-part';
    let allComponents = document.querySelectorAll(modelClass);
    let line = allComponents[0];
    let confidenceArea = allComponents[1];
    let focus = allComponents[2];
    if (line.style.display !== 'none') {
      line.style.display = 'none';
      confidenceArea.style.display = 'none';
    } else {

    }
  }

  render () {
    return <button onClick={this.handleClick}>
      {model}
    </button>;
  }
}

export default lineGraphToggle;