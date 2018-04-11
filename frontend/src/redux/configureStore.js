import { createStore, combineReducers, applyMiddleware } from 'redux';
import thunk from 'redux-thunk';
import { routerMiddleware, routerReducer } from 'react-router-redux';
import createHistory from 'history/createBrowserHistory';
import { composeWithDevTools } from 'redux-devtools-extension';
import { i18nState } from 'redux-i18n';
import user from 'redux/modules/user';

const env = process.env.NODE_ENV; // process: node.js의 전체 정보(실행환경...)를 가지고 있는 변수

const history = createHistory(); // 페이지 이동 기록(뒤로가기, 앞으로가기 등으로 이용 가능)

// redux와 함께 사용할 middlewares 목록
const middlewares = [
	thunk,
	routerMiddleware(history), // history와 router의 싱크를 위함
];

if(env === 'development'){ // 개발환경이면 Redux Logger 사용
    const { logger } = require('redux-logger');
    middlewares.push(logger);
}

// 생성된 reducer를 합침
const reducer = combineReducers({
    user,
    routing: routerReducer,
    i18nState,
});

// store 생성
let store;
if(env === 'development'){ // 개발환경이면 Redux의 Debugging을 위해 Reactotron에서 store 생성
    store = initialState => 
        createStore(reducer, composeWithDevTools(applyMiddleware(...middlewares)));
} else {
    store = initialState => 
        createStore(reducer, applyMiddleware(...middlewares));
}

export { history }; // routerMiddleware에 설정한 history를 index.js와 공유할 수 있도록함.

export default store();