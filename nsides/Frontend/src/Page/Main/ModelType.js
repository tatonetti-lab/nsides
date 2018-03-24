import React from 'react';
import { drawTimeSeriesGraph } from '../../Helpers/graphing';

class ModelType extends React.Component {
  constructor (props) {
    super (props);
    this.state = {

    };
    this.handleChange = this.handleChange.bind(this);
  }

  handleChange (e) {
    let { selectedIndex, value } = e.target;
    console.log(selectedIndex, value, this.props.drugEffectData);
    if (selectedIndex !== undefined) {
      let modelData = this.props.drugEffectData[selectedIndex];
      let title1 = "Proportional Reporting Ratio over time";
      let title2 = "Number of reports by year";
      drawTimeSeriesGraph(modelData.estimates, modelData.nreports, title1, title2, '%Y', false, modelData.model);
    }
  }

  render () {
    let data = this.props.drugEffectData;
    // console.log('data', data);
    if (data.length === 0) {
      return null;
    }
    let options = data.map((dataset, i) => {
      return <option key={i} 
              value={dataset.model}>
              {dataset.model}
            </option>;
    })
    return (
    <div className='standardStyle'>   
      Modeloptions: 
      <select className='model-types' onChange={this.handleChange}>
        {options}
      </select>
    </div>
    )
  }
}

export default ModelType;