import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration


required_conan_version = ">=1.29.1"

class ResiprocateConan(ConanFile):
    name = "resiprocate"
    description = "The project is dedicated to maintaining a complete, correct, and commercially usable implementation of SIP and a few related protocols. "
    topics = ("sip", "voip", "communication", "signaling")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.resiprocate.org"
    license = "VSL-1.0"
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False],
               "with_ssl": [True, False],
               "with_postgresql": [True, False],
               "with_mysql": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False,
                       "with_ssl": True,
                       "with_postgresql": True,
                       "with_mysql": True}
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.settings.os in ("Windows", "Macos"):
            raise ConanInvalidConfiguration("reSIProcate is not support on {}.".format(self.settings.os))
        if self.options.with_ssl:
            self.requires("openssl/1.1.1h")
        if self.options.with_postgresql:
            self.requires("libpq/11.5")
        if self.options.with_mysql:
            self.requires("libmysqlclient/8.0.17")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        configure_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-ssl={}".format(yes_no(not self.options.with_ssl)),
            "--with-mysql={}".format(yes_no(not self.options.with_mysql)),
            "--with-postgresql={}".format(yes_no(not self.options.with_postgresql)),
            "--with-pic={}".format(yes_no(not self.options.fPIC))
        ]

        self._autotools.configure(configure_dir=self._source_subfolder, args=configure_args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(os.path.join(self.package_folder, "share")))
        tools.remove_files_by_mask(os.path.join(self.package_folder), "*.la")

    def package_info(self):
        self.cpp_info.libs = ["resip", "rutil", "dum", "resipares"]
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
