#!/usr/bin/env python
# coding: UTF-8
# @copyright ©2013, Rodrigo Cacilhας <batalema@cacilhas.info>
#                   Cesar Barros <cesar.barros@gmail.com>

import logging
from unittest import main, TestCase
import flask_reportable_error


class TestInit(TestCase):

    class Application(object):

        def __init__(self):
            self.handlers = {}
            self.config = {}
            self.logged = []
            self.logger = type('Logger', (object, ), {
                'log': lambda logger, *args: self.logged.append(args),
            })()

        def errorhandler(self, exc):
            def register(callback):
                self.handlers[exc] = callback
            return register

    def setUp(self):
        cls = type(self)
        app = self.app = cls.Application()
        flask_reportable_error.init(app)
        self.handler = app.handlers[
            flask_reportable_error.ReportableErrorMixin
        ]

    def test_register_application(self):
        self.assertEqual(self.handler.__name__,
                         'reportable_error_handler')
        self.assertEqual(flask_reportable_error.ReportableErrorMixin.app,
                         self.app)

    def test_handle_error_500(self):
        s = 'test reportable error'
        exc = flask_reportable_error.ReportableErrorMixin(s)
        report, status_code, headers = self.handler(exc)
        self.assertEqual(report, s)
        self.assertEqual(status_code, 500)
        self.assertEqual(headers, {})

    def test_log_error(self):
        s = 'test reportable error'
        exc = flask_reportable_error.ReportableErrorMixin(s)
        self.handler(exc)
        self.assertEqual(self.app.logged, [
            (logging.DEBUG, '(%s) %s', 'ReportableErrorMixin', exc),
        ])

    def test_log_deeper(self):
        s = 'test reportable error'
        app = self.app
        app.config['REPORTABLE_ERROR'] = {
            'LOGLEVEL': logging.ERROR,
        }
        exc = flask_reportable_error.ReportableErrorMixin(s)
        self.handler(exc)
        self.assertEqual(app.logged, [
            (logging.ERROR, '(%s) %s', 'ReportableErrorMixin', exc),
        ])

    def test_handle_error_400(self):
        s = 'test reportable error'
        self.app.config['REPORTABLE_ERROR'] = {
            'DEFAULT_STATUS_CODE': 400,
        }
        exc = flask_reportable_error.ReportableErrorMixin(s)
        report, status_code, headers = self.handler(exc)
        self.assertEqual(report, s)
        self.assertEqual(status_code, 400)
        self.assertEqual(headers, {})

    def test_handle_own_status(self):
        s = 'test reportable error'
        exc = flask_reportable_error.ReportableErrorMixin(s)
        exc.status_code = 404
        report, status_code, headers = self.handler(exc)
        self.assertEqual(report, s)
        self.assertEqual(status_code, 404)
        self.assertEqual(headers, {})



class TestReportableErrorMixin(TestCase):

    def test_reportable_error_report(self):
        s = 'test reportable error'
        exc = flask_reportable_error.ReportableErrorMixin(s)
        self.assertEqual(exc.report(), s)

    def test_reportable_factory_return_reportable_error(self):
        exc_class = flask_reportable_error.reportable(ValueError)
        self.assertTrue(issubclass(exc_class,
                                   flask_reportable_error.ReportableErrorMixin))
        self.assertTrue(issubclass(exc_class, ValueError))

    def test_reportable_factory_response_report_error(self):
        s = 'test reportable error'
        exc = flask_reportable_error.reportable(ValueError)(s)
        self.assertEqual(exc.report(), s)

    def test_reportable_factory_response_be_memoized(self):
        exc1 = flask_reportable_error.reportable(ValueError)
        exc2 = flask_reportable_error.reportable(ValueError)
        exc3 = flask_reportable_error.reportable(AttributeError)
        self.assertIs(exc1, exc2)
        self.assertNotEqual(exc1, exc3)


if __name__ == '__main__':
    main()
