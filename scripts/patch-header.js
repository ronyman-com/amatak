const fs = require('fs');
const path = require('path');

const headerPath = path.join(
  __dirname,
  '../node_modules/get-uv-event-loop-napi-h/include/get-uv-event-loop-napi.h'
);

const content = fs.readFileSync(headerPath, 'utf8');
const fixedContent = content.replace(
  'get_uv_event_loop_fn get_uv_event_loop = node_api_get_uv_event_loop;',
  'get_uv_event_loop_fn get_uv_event_loop = reinterpret_cast<get_uv_event_loop_fn>(node_api_get_uv_event_loop);'
);

fs.writeFileSync(headerPath, fixedContent);
console.log('Successfully patched get-uv-event-loop-napi.h');