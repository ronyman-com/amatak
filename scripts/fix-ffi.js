const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

try {
  // Fix ffi-napi header
  const headerPath = path.join(
    __dirname,
    '../node_modules/get-uv-event-loop-napi-h/include/get-uv-event-loop-napi.h'
  );
  
  if (fs.existsSync(headerPath)) {
    let content = fs.readFileSync(headerPath, 'utf8');
    content = content.replace(
      'get_uv_event_loop_fn get_uv_event_loop = node_api_get_uv_event_loop;',
      'get_uv_event_loop_fn get_uv_event_loop = reinterpret_cast<get_uv_event_loop_fn>(node_api_get_uv_event_loop);'
    );
    fs.writeFileSync(headerPath, content);
  }

  // Rebuild
  execSync('npm rebuild ffi-napi --update-binary', { stdio: 'inherit' });
} catch (err) {
  console.error('Postinstall failed:', err);
  process.exit(1);
}