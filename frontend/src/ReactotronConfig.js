import Reactotron from 'reactotron-react-js';
import { reactotronRedux } from 'reactotron-redux';

Reactotron.configure({ name: 'frontend' })
    .use(reactotronRedux())
    .connect();

export default Reactotron;
