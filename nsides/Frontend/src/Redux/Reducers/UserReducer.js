let start = {
  session: {},
  requestedSession: false
};

const UserReducer = (state = start, action) => {
  let newState = Object.assign({}, state);
  // console.log('home state', newState, action);
  switch (action.type) {
    case `UPDATE USER INFO`:
      // console.log('update user info', newState);
      newState.session = action.payload;
      newState.requestedSession = true;
      return newState;
    default:
      return newState;
  }
}

export default UserReducer;