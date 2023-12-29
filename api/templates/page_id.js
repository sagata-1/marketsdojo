(function () {
    if (typeof window.datadog_attributes != 'object')
      window.datadog_attributes = {}
    window.datadog_attributes['pageType'] = 'other'

    // Log experiment enrolment
    var experiment_data_string = "" + "!"
    window.datadog_attributes['experiments'] = experiment_data_string
  })()

//]]