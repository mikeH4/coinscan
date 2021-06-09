const safeHandler = async (func,{
    log=null,
    logError=true,
    throwError=false,
}) => {
    try {
        return await func()
    } catch (error) {
        if (logError) {
            console.error(error)
        } if (log !== null) {
            console.log(log)
        } if (throwError) {
            throw error
        }
        return null
    }
}
exports.safeHandler = safeHandler