const updateUserSession = (session) => {
  // console.log('triggered', session);
  const action = {
    type: `UPDATE USER INFO`,
    payload: session
  };
  return action;
}

const all = {
  updateUserSession
};

export default all;
export {
  updateUserSession
}