const bind = (dispatch, action) => {
  console.log('invoked');
  return function (...args) {
    console.log(...args, 'arguments');
    return dispatch(action(...args));
  };
};

const escapeRegexCharacters = function (str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
};

const all = {
  bind,
  escapeRegexCharacters
};

export default all;
export {
  bind,
  escapeRegexCharacters
};