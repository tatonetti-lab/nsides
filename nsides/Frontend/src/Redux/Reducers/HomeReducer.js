let start = {
  drugEffectData: [],
  selectedModel: null
};

const HomeReducer = (state = start, action) => {
  let newState = Object.assign({}, state);
  // console.log('home state', newState);
  switch (action.type) {
    case `HOMEACTION SET DRUG EFFECT DATA`:
      newState.drugEffectData = action.payload;
      return newState;
    case `HOMEACTION SET SELECTED MODEL`:
      newState.selectedModel = action.payload;
      return newState;
    default:
      return state;
  }
}

export default HomeReducer;