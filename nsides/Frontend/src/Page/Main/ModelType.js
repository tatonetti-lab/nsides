import React from 'react';

class ModelType extends React.Component {
  constructor (props) {
    super (props);
    this.state = {

    };

  }

  render () {
    let data = this.props.drugEffectData;
    if (data.length === 0) {
      return null;
    }
    let options = data.map((dataset, i) => {
      return <option key={i} value={dataset.model}>{dataset.model}</option>;
    })
    return (
    <div className='standardStyle'>   
      Modeloptions: 
      <select className='model-types'>
        {options}
      </select>
    </div>
    )
  }
}

export default ModelType;