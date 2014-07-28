module.exports = function(grunt) {
  // Project configuration.
  grunt.initConfig({

    pkg: grunt.file.readJSON('package.json'),
    jekyllConfig: grunt.file.readYAML('_config.yml'),

    jekyll: {
      build: {
      },
      serve: {
        options: {
          serve: true,
          port: 9000,
          watch: true,
        }
      }
    },

    vulcanize: {
      options: {
        strip: true,
        csp: false,
        inline: true
      },
      build: {
        files: {
          'elements/elements.vulcanized.html': 'elements/elements.html'
        },
      }
    },

    watch: {
      elements: {
        files: ['elements/**/*.html'],
        tasks: ['vulcanize'],
        options: {
          spawn: false,
        }
      }
    },

    concurrent: {
      options: {
        logConcurrentOutput: true,
        limit: 5
      },
      target1: [
        'vulcanize',
        'jekyll:serve',
        'watch'
      ]
    }

  });

  // Plugin and grunt tasks.
  require('load-grunt-tasks')(grunt);

  // Default task
  // Task to run vulcanize, jekyll, app engine server, compass watch, vulcanize watch
  grunt.registerTask('default', ['concurrent']);

  // Task to run vulcanize and build the jekyll site
  grunt.registerTask('build', ['vulcanize', 'jekyll:build']);
};
