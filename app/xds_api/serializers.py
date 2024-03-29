import logging

from django.contrib.auth import authenticate
from openlxp_notifications.management.commands.conformance_alerts import \
    send_log_email_with_msg
from openlxp_notifications.models import SenderEmailConfiguration
from rest_framework import serializers

from core.models import (CourseDetailHighlight, CourseInformationMapping,
                         Experience, InterestList, SavedFilter,
                         SearchSortOption, XDSConfiguration,
                         XDSUIConfiguration, XDSUser)

logger = logging.getLogger('dict_config_logger')


class FilteredListSerializer(serializers.ListSerializer):
    """Extends the ListSerializer to enable us to filter \
        out data before serializing"""

    def to_representation(self, data):
        data = data.filter(active=True)
        return super(FilteredListSerializer, self).to_representation(data)


class OrderedListSerializer(serializers.ListSerializer):
    """Extends the ListSerializer to enable us to filter \
        out data and sort it before serializing"""

    def to_representation(self, data):
        data = data.filter(active=True).order_by('rank')
        return super(OrderedListSerializer, self).to_representation(data)


class XDSConfigurationSerializer(serializers.ModelSerializer):
    """Serializes the XDSConfiguration Model"""

    class Meta:
        model = XDSConfiguration

        fields = ['target_xis_metadata_api']


class SearchSortOptionSerializer(serializers.ModelSerializer):
    """Serializes the SearchSortOption Model"""

    class Meta:
        list_serializer_class = FilteredListSerializer
        model = SearchSortOption

        fields = ['display_name', 'field_name', 'active',
                  'xds_ui_configuration']


class CourseDetailHighlightSerializer(serializers.ModelSerializer):
    """Serializes the CourseDetailHighlight Model"""

    class Meta:
        list_serializer_class = OrderedListSerializer
        model = CourseDetailHighlight

        fields = ['display_name', 'field_name', 'active',
                  'xds_ui_configuration', 'highlight_icon', ]


class CourseInformationMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseInformationMapping
        fields = ['course_title', 'course_description', 'course_url']


class XDSUIConfigurationSerializer(serializers.ModelSerializer):
    """Serializes the XDSUIConfiguration Model"""

    search_sort_options = SearchSortOptionSerializer(many=True, read_only=True)
    course_highlights = CourseDetailHighlightSerializer(many=True,
                                                        read_only=True)
    course_information = CourseInformationMappingSerializer(read_only=True)

    class Meta:
        model = XDSUIConfiguration

        exclude = ('xds_configuration',)


# user serializer
class XDSUserSerializer(serializers.ModelSerializer):
    """Serializes the XDSUser model"""

    class Meta:
        model = XDSUser
        fields = ('id', 'email', 'first_name', 'last_name')


# register serializer
class RegisterSerializer(serializers.ModelSerializer):
    """Serializes the registration form from the API"""

    class Meta:
        model = XDSUser
        fields = ('id', 'email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Create a user"""
        user = XDSUser.objects \
            .create_user(validated_data['email'],
                         validated_data['password'],
                         first_name=validated_data['first_name'],
                         last_name=validated_data['last_name'])

        return user


# login serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """Validate a user is active in the system"""

        # the user object
        user = authenticate(**data)

        if user and user.is_active:
            return user

        # returns when user is inactive or not in the system
        raise serializers.ValidationError('Incorrect Credentials')


class ExperienceSerializer(serializers.ModelSerializer):
    """Serializes the Course model"""

    class Meta:
        model = Experience
        fields = ['metadata_key_hash']


class InterestListSerializer(serializers.ModelSerializer):
    """Serializes the interest list model"""
    owner = XDSUserSerializer(read_only=True)
    subscribers = XDSUserSerializer(many=True, read_only=True)

    class Meta:
        model = InterestList
        fields = '__all__'

    def create(self, validated_data):
        name = validated_data.get("name")
        description = validated_data.get("description")
        owner = validated_data.get("owner")
        return InterestList.objects.create(name=name,
                                           description=description,
                                           owner=owner)

    def update(self, instance, validated_data):
        instance.owner = validated_data.get('owner', instance.owner)
        instance.description = validated_data.get('description',
                                                  instance.description)
        instance.name = validated_data.get('name', instance.name)
        experiences = validated_data.get('experiences')
        # for each experience in the experience list, we add the experience to
        # the current interest list
        course_added_count = 0
        for course in experiences:
            instance.experiences.add(course)
            course_added_count += 1

        # for each saved experience in the experience list, we remove the
        # experience if we don't find it in the passed in the updated list
        for exp in instance.experiences.all():
            if exp not in experiences:
                instance.experiences.remove(exp)

        #  writing content to file
        msg = ("Count of New Courses added: " + str(course_added_count))

        list_subscribers = []
        for each_subscriber in instance.subscribers.all():
            list_subscribers.append(each_subscriber.email)

        # Getting sender email id
        sender_email_configuration = SenderEmailConfiguration.objects.first()
        sender = sender_email_configuration.sender_email_address

        instance.save()
        send_log_email_with_msg(list_subscribers, sender, msg)
        return instance


class SavedFilterSerializer(serializers.ModelSerializer):
    """Serializes the Saved filter model"""
    owner = XDSUserSerializer(read_only=True)

    class Meta:
        model = SavedFilter
        fields = '__all__'

    def create(self, validated_data):
        return SavedFilter.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.owner = validated_data.get('owner', instance.owner)
        instance.name = validated_data.get('name', instance.name)
        instance.query = validated_data.get('query', instance.query)
        instance.save()

        return instance
