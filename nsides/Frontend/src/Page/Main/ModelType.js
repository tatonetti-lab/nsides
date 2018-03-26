import React from 'react';
import { drawTimeSeriesGraph } from '../../Helpers/graphing';

class ModelType extends React.Component {
  constructor (props) {
    super (props);
    this.state = {

    };
    this.handleChange = this.handleChange.bind(this);
    // this.handleClick = this.handleClick.bind(this);
  }

  handleChange (e) {
    let { selectedIndex, value } = e.target;
    console.log(e.target.value)
    console.log(selectedIndex, value, this.props.drugEffectData);
    if (selectedIndex !== undefined) {
      let modelData = this.props.drugEffectData[selectedIndex];
      let title1 = "Proportional Reporting Ratio over time";
      let title2 = "Number of reports by year";
      drawTimeSeriesGraph(modelData.estimates, modelData.nreports, title1, title2, '%Y', false, modelData.model);
    }
  }

  // handleClick (e) {
  //   e.preventDefault();
  //   e.target.parentNode.value = e.target.value;
  // }

  render () {
    let { selectedModel, drugEffectData } = this.props;
    console.log(this.props);
    // console.log('data', data);
    if (drugEffectData.length === 0 || selectedModel === null) {
      return null;
    }
    let options = drugEffectData.map((dataset, i) => {
      return <option key={i} 
              value={dataset.model}>
              {dataset.model}
            </option>;
    })
    return (
    <div className='standardStyle'>   
      Model Options: 
      <select className='model-types' onChange={this.handleChange}>
        {options}
      </select>
    </div>
    )
  }
}

export default ModelType;