//////////////////////////////////////////////////
// dependencies
//////////////////////////////////////////////////
// built-ins
var bodyParser   = require('body-parser');
var compression  = require('compression');
var cookieParser = require('cookie-parser');
var express      = require('express');
var favicon      = require('serve-favicon');
var fs           = require("fs");
var path         = require('path');

// custom
var logger = require('./logger');
// testting

//////////////////////////////////////////////////
// initialization
//////////////////////////////////////////////////
var app = express();

// detect development mode
app.locals.development_mode = app.get('env') === 'development';

// configure app details
app.locals.site_name = "HokieGPT";

// configure view engine
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

// miscellaneous resources
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());


//////////////////////////////////////////////////
// routes
//////////////////////////////////////////////////
// favicon
app.use(favicon(path.join(__dirname, 'public/images/favicon.ico')))

// standard routes
app.use('/',            require('./routes/route_index'));

// static routes - directories
app.use('/js',     express.static(path.join(__dirname, 'public/js'),     {maxAge : 1}));
app.use('/css',    express.static(path.join(__dirname, 'public/css'),    {maxAge : 1}));
app.use('/images', express.static(path.join(__dirname, 'public/images'), {maxAge : 1}));

//////////////////////////////////////////////////
// error handling
//////////////////////////////////////////////////
// catch 404 and forward to error handler
app.use(function(req, res, next) {
  var err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = app.locals.development_mode ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});


//////////////////////////////////////////////////
// initialization log output
//////////////////////////////////////////////////
logger.info('node.js : ' + process.version);
logger.info('NODE_ENV: ' + app.get('env'));


module.exports = app;