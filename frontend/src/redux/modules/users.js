// imports

// actions

// action creators

// initial state
const initialState = {
    isLoggedIn: localStorage.getItem("jwt") || false, // jwt 저장. localStorage: 브라우저에서 사용할 값을 저장하는 곳. 다른 웹페이지와 공유되지는 않음.
};

// reducer
function reducer(state=initialState, action){
    switch(action.type){
        default:
            return state;
    }
}

// reducer functions

// exports

// reducer export
export default reducer;