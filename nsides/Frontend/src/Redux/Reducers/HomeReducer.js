let start = {
  drugEffectData: []
};

const HomeReducer = (state = start, action) => {
  let newState = Object.assign({}, state);
  // console.log('home state', newState);
  switch (action.type) {
    case `SET DRUG EFFECT DATA`:
      newState.drugEffectData = action.payload;
      return newState;
    default:
      return state;
  }
}

export default HomeReducer;