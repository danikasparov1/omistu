// website_candidate_profile/static/src/js/candidate_profile.js
odoo.define('recruitment_website.custom_storage', function (require) {
    'use strict';

    var $ = require('jquery');

    $(document).ready(function () {
        // Retrieve stored profiles
        function getProfiles() {
            var profiles = localStorage.getItem('candidateProfiles');
            return profiles ? JSON.parse(profiles) : [];
        }

        // Store profiles
        function storeProfiles(profiles) {
            localStorage.setItem('candidateProfiles', JSON.stringify(profiles));
        }

        // Add a new profile
        function addProfile(profile) {
            var profiles = getProfiles();
            profiles.push(profile);
            storeProfiles(profiles);
        }

        // Display profiles
        function displayProfiles() {
            var profiles = getProfiles();
            var profileContainer = $('#profileContainer');
            profileContainer.empty();
            profiles.forEach(function(profile, index) {
                var profileHtml = `<div class="profile">
                    <h4>Education ${index + 1}</h4>
                    <p><strong>Institution:</strong> ${profile.institution}</p>
                    <p><strong>Degree:</strong> ${profile.degree}</p>
                    <p><strong>Field of Study:</strong> ${profile.fieldOfStudy}</p>
                    <p><strong>Start Date:</strong> ${profile.startDate}</p>
                    <p><strong>End Date:</strong> ${profile.endDate}</p>
                </div>`;
                profileContainer.append(profileHtml);
            });
        }

        // Handle form submission
        $('#educationForm').on('submit', function (e) {
            e.preventDefault();
            var profile = {
                institution: $('#institution').val(),
                degree: $('#degree').val(),
                fieldOfStudy: $('#fieldOfStudy').val(),
                startDate: $('#startDate').val(),
                endDate: $('#endDate').val()
            };
            addProfile(profile);
            displayProfiles();
            this.reset();
        });

        // Initial display
        displayProfiles();
    });
});
