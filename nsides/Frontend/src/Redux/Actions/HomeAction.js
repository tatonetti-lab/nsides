const setDrugEffectData = (data) => {
  let action = {
    type: `SET DRUG EFFECT DATA`,
    payload: data
  }
  return action;
};

let all = {
  setDrugEffectData
};

export default all;
export {
  setDrugEffectData
};