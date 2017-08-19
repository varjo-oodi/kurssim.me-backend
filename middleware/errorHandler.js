
module.exports.handleErrors = (err, req, res, next) => {
  if (err) {
    const statusCode = err.statusCode !== undefined ? err.statusCode : 500;
    console.log(err)    
    if (err.message !== undefined) {
      res.status(statusCode).json(err);
    } else {
      res.status(statusCode).send({
        message: "Something caused an internal server error",
        stack: err.stack,
      });
    }
  } else {
    next();
  }
}