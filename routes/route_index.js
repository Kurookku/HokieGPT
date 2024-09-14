"use strict";
const express   = require('express');
const router    = express.Router();

// CONSTANTS

// compile the template
const app = express();

// handle GET request
router.get('/', async function(request, response, next) {
  ////////////////////////////////////////////
  // send response
  ////////////////////////////////////////////
  response.setHeader('Cache-Control', 'public, max-age=30');
  response.status(200);

  response.send("Hello Hokies!")

  // response.render(path.join(app.get('views'), 'index.pug'), {
  //     title: request.app.locals.site_name
  // })
});

module.exports = router