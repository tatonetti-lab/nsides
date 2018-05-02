const bind = (dispatch, action) => {
  console.log('invoked');
  return function (...args) {
    console.log(...args, 'arguments');
    return dispatch(action(...args));
  };
};

const all = {
  bind
};

export default all;
export {
  bind
};