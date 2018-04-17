// imports

// actions
const SAVE_TOKEN = "SAVE_TOKEN"

// action creators
function saveToken(token){
    return{
        type: SAVE_TOKEN,
        token
    }
}

// API actions
function facebookLogin(access_token){ // access_token은 backend에 보낼 토큰이다.
  return dispatch => {
    fetch("/users/login/facebook/", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        access_token
      })
    })
    .then(response => response.json())
    .then(json => {
      if(json.token){
          localStorage.setItem('jwt', json.token)
          dispatch(saveToken(json.token))
      }
    })
    .catch(err => console.log(err))
  }
}

// initial state
const initialState = {
  isLoggedIn: localStorage.getItem("jwt") ? true : false, // jwt 저장. localStorage: 브라우저에서 사용할 값을 저장하는 곳. 다른 웹페이지와 공유되지는 않음.
};

// reducer
function reducer(state=initialState, action){
  switch(action.type){
    case SAVE_TOKEN:
      return applySetToken(state, action)
    default:
      return state;
  }
}

// reducer functions
function applySetToken(state, action){
    const {token} = action

    return {
        ...state,
        isLoggedIn: true,
        token
    }
}

// exports
const actionCreators = {
    facebookLogin
}

export {actionCreators}

// reducer export
export default reducer;