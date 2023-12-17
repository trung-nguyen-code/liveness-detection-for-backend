import { Buffer } from 'buffer';
import { MEDIA_URL } from './constants';
import origin from './origin.json'
const md5 = require('md5');

const FILE_EXT = 'jpg'
export const bodyMapping = ["Peu importe", "Mince", "Musclé", "Normal", "Quelque forme", "Enrobé", "Autre"]
export const localisationMapping = ["Doesn't matter", "Same city", "Same region", "Same department", "Same country",]
export const familySituationMapping = {
    0: "-", 1: "Jamais mariée", 3: "Séparé", 4: "Divorcé", 5: "Veuf", 88: "no matter", 99: "keep_it_for_myself"
}
export const religioutMapping = {
    0: "Non", 1: "Oui", 88: "no matter", 99: "keep_it_for_myself"
}
export const degreeMapping = {
    0: "Peu importe", 1: "Niveau lycée et inférieur", 2: "Bac", 3: "Bac +2", 4: "Bac +3", 5: "Bac +4", 6: "Bac +5 et plus", 99: "keep_it_for_myself"
}
export const hasChildrenMapping = {
    0: "Non", 1: "Oui, 1 enfant", 2: "Oui, 2 enfants", 3: "Oui, 3 enfants", 4: "Oui, + de 3 enfants", 5: "-", 88: "no matter"
}
export const wantChildrenMapping = {
    0: "-", 1: "Oui", 2: "Non", 5: "Peu importe"
}

export const fumesMapping = {
    1: 'smoke_cigarette', 2: 'smoke_ecig', 3: 'smoke_try_stop_entity_man', 0: 'smoke_non', 88: 'no_matter',
}
export const salatPratiqueMapping = {
    0: 'practice_salat_everyday',
    1: 'practice_salat_sometimes',
    2: 'practice_salat_never',
    99: 'keep_it_for_myself',
}
export const veilMapping = {
    1: 'wear_veil_hijab',
    2: 'wear_veil_turban',
    0: 'wear_veil_no',
}

export const eatHalalMapping = {
    0: 'eat_halal_no',
    1: 'eat_halal_yes',
    99: 'keep_it_for_myself',
}

export function getOriginName(id) {
    return origin.find(item => item.id === id)
}
export const base64 = {
    decode: (s) => Buffer.from(s, 'base64'),
    encode: (b) => Buffer.from(b).toString('base64'),
};

const reverseString = (string) => {
    return string.split('').reverse().join('');
};

const createUserDirPath = (id, gender) => {
    let encoded = base64.encode(`${id}`);
    encoded = reverseString(encoded);
    encoded = encoded.replace(/=/g, '_');
    encoded = encoded.replace(/\//g, '$');
    encoded = encoded.replace(/\+/g, '-');

    return `${gender}/${Math.floor(id / 1000)}/${encoded}`;
};
const createPhotoFileName = (photoId, id, photoHash, photoType, photoSize) => {
    let encoded = base64.encode(`${photoId}`);
    encoded = encoded.replace(/=/g, '_');
    encoded = encoded.replace(/\//g, '$');
    encoded = encoded.replace(/\+/g, '-');
    encoded = reverseString(encoded);

    const data = `${id}${photoType}${photoSize}`;
    const formatPath = md5(data);

    return `${encoded}${photoHash}${formatPath.substr(0, 5)}`;
};

export const createNasPath = (photo) => {
    const { id, gender, photoId, photoHash, photoType, photoSize } = photo;
    const media_url = process.env.PHOTO_DOMAIN ? process.env.PHOTO_DOMAIN : MEDIA_URL;
    return `${media_url}/${createUserDirPath(id, gender)}/${createPhotoFileName(photoId, id, photoHash, photoType, photoSize)}.${FILE_EXT
        }`;
};